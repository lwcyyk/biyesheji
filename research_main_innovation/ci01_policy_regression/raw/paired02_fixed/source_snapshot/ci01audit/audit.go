// Observation only: records stages and I/O counts; never returns policy decisions.
package ci01audit
import "sync"
type Event struct {Stage string `json:"stage"`;Passed bool `json:"passed"`;Detail string `json:"detail,omitempty"`}
var mu sync.Mutex
var active bool
var events []Event
var counters map[string]int
func Begin(){mu.Lock();defer mu.Unlock();active=true;events=[]Event{};counters=map[string]int{}}
func End()([]Event,map[string]int){mu.Lock();defer mu.Unlock();active=false;return append([]Event{},events...),counters}
func Record(stage string,passed bool,detail string){mu.Lock();defer mu.Unlock();if active{events=append(events,Event{stage,passed,detail})}}
func Count(kind string){mu.Lock();defer mu.Unlock();if active{counters[kind]++}}
